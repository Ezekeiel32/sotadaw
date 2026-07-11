/* ------------------------------------------------------------
name: "chip_bass"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn ChipBass -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __ChipBass_H__
#define  __ChipBass_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS ChipBass
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float ChipBass_faustpower2_f(float value) {
	return value * value;
}

class ChipBass : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec1[2];
	float fConst2;
	float fRec2[2];
	float fConst3;
	float fConst4;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst5;
	float fRec4[2];
	float fVec2[2];
	float fConst6;
	int IOTA0;
	float fVec3[4096];
	float fConst7;
	float fRec3[2];
	FAUSTFLOAT fHslider3;
	float fConst8;
	FAUSTFLOAT fHslider4;
	FAUSTFLOAT fHslider5;
	float fRec0[3];
	
 public:
	ChipBass() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn ChipBass -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "chip_bass.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/pole:author", "Julius O. Smith III");
		m->declare("filters.lib/pole:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/pole:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "chip_bass");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/sawN:author", "Julius O. Smith III");
		m->declare("oscillators.lib/sawN:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		fConst2 = 1.0f / std::max<float>(1.0f, 0.08f * fConst0);
		fConst3 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst4 = 1.0f / fConst3;
		fConst5 = 1.0f / fConst0;
		fConst6 = 0.25f * fConst0;
		fConst7 = 0.5f * fConst0;
		fConst8 = 2.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(3.8e+03f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.7f);
		fHslider2 = FAUSTFLOAT(1.1e+02f);
		fHslider3 = FAUSTFLOAT(16.0f);
		fHslider4 = FAUSTFLOAT(1.15f);
		fHslider5 = FAUSTFLOAT(0.85f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec4[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fVec2[l5] = 0.0f;
		}
		IOTA0 = 0;
		for (int l6 = 0; l6 < 4096; l6 = l6 + 1) {
			fVec3[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec3[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec0[l8] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual ChipBass* clone() {
		return new ChipBass();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("chip_bass");
		ui_interface->addHorizontalSlider("decay", &fHslider1, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.1f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("drive", &fHslider4, FAUSTFLOAT(1.15f), FAUSTFLOAT(0.5f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(1.1e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(1e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.85f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("steps", &fHslider3, FAUSTFLOAT(16.0f), FAUSTFLOAT(4.0f), FAUSTFLOAT(64.0f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("tone", &fHslider0, FAUSTFLOAT(3.8e+03f), FAUSTFLOAT(4e+02f), FAUSTFLOAT(9e+03f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / ChipBass_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -1.4142135f) / fSlow0 + 1.0f;
		float fSlow4 = 1.0f / ((fSlow2 + 1.4142135f) / fSlow0 + 1.0f);
		float fSlow5 = float(fButton0);
		int iSlow6 = fSlow5 == 0.0f;
		float fSlow7 = 0.45f / std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow8 = float(fHslider2);
		float fSlow9 = std::max<float>(fSlow8, 23.44895f);
		float fSlow10 = std::max<float>(2e+01f, std::fabs(fSlow9));
		float fSlow11 = fConst5 * fSlow10;
		float fSlow12 = fConst6 / fSlow10;
		float fSlow13 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst7 / fSlow9));
		int iSlow14 = int(fSlow13);
		int iSlow15 = iSlow14 + 1;
		float fSlow16 = std::floor(fSlow13);
		float fSlow17 = fSlow13 - fSlow16;
		float fSlow18 = fSlow16 + (1.0f - fSlow13);
		float fSlow19 = float(fHslider3);
		float fSlow20 = fConst8 * fSlow8 * fSlow19;
		float fSlow21 = 2.0f * (float(fHslider4) / fSlow19);
		float fSlow22 = float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow5;
			iRec1[0] = iSlow6 * (iRec1[1] + 1);
			fRec2[0] = fSlow5 + fRec2[1] * float(fVec1[1] >= fSlow5);
			float fTemp0 = ((1 - iVec0[1]) ? 0.0f : fSlow11 + fRec4[1]);
			fRec4[0] = fTemp0 - std::floor(fTemp0);
			float fTemp1 = ChipBass_faustpower2_f(2.0f * fRec4[0] + -1.0f);
			fVec2[0] = fTemp1;
			float fTemp2 = fSlow12 * float(iVec0[1]) * (fTemp1 - fVec2[1]);
			fVec3[IOTA0 & 4095] = fTemp2;
			fRec3[0] = 0.999f * fRec3[1] + fTemp2 - (fSlow18 * fVec3[(IOTA0 - iSlow14) & 4095] + fSlow17 * fVec3[(IOTA0 - iSlow15) & 4095]);
			fRec0[0] = fSlow22 * tanhf(fSlow21 * std::floor(fSlow20 * fRec3[0] + 0.5f)) * std::max<float>(0.0f, std::min<float>(fConst4 * fRec2[0], std::max<float>(fSlow7 * (fConst3 - fRec2[0]) + 1.0f, 0.55f)) * (1.0f - fConst2 * float(iRec1[0]))) - fSlow4 * (fSlow3 * fRec0[2] + fSlow1 * fRec0[1]);
			float fTemp3 = fSlow4 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp3);
			output1[i0] = FAUSTFLOAT(fTemp3);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec1[1] = iRec1[0];
			fRec2[1] = fRec2[0];
			fRec4[1] = fRec4[0];
			fVec2[1] = fVec2[0];
			IOTA0 = IOTA0 + 1;
			fRec3[1] = fRec3[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
