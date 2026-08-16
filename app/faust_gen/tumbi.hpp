/* ------------------------------------------------------------
name: "tumbi"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Tumbi -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Tumbi_H__
#define  __Tumbi_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Tumbi
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

static float Tumbi_faustpower2_f(float value) {
	return value * value;
}

class Tumbi : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst6;
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	float fConst7;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec3[2];
	float fConst8;
	float fConst9;
	float fConst10;
	int iRec4[2];
	int IOTA0;
	float fVec1[256];
	FAUSTFLOAT fHslider2;
	float fConst11;
	float fRec2[3];
	float fRec5[2];
	FAUSTFLOAT fHslider3;
	float fVec2[2048];
	float fRec1[3];
	float fRec0[3];
	float fConst12;
	
 public:
	Tumbi() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Tumbi -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/fdelay4:author", "Julius O. Smith III");
		m->declare("delays.lib/fdelayltv:author", "Julius O. Smith III");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "tumbi.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "tumbi");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
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
		float fConst1 = std::tan(1947.7875f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / Tumbi_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -0.2f) / fConst1 + 1.0f;
		float fConst5 = (fConst3 + 0.2f) / fConst1 + 1.0f;
		fConst6 = 1.0f / fConst5;
		fConst7 = 3.1415927f / fConst0;
		fConst8 = std::max<float>(1.0f, 0.0003f * fConst0);
		fConst9 = 1.0f / fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.0022f * fConst0);
		fConst11 = 0.09f * fConst0;
		fConst12 = 0.3f / (fConst1 * fConst5);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.8f);
		fHslider1 = FAUSTFLOAT(0.7f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider2 = FAUSTFLOAT(392.0f);
		fHslider3 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec3[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec4[l2] = 0;
		}
		IOTA0 = 0;
		for (int l3 = 0; l3 < 256; l3 = l3 + 1) {
			fVec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec5[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2048; l6 = l6 + 1) {
			fVec2[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec1[l7] = 0.0f;
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
	
	virtual Tumbi* clone() {
		return new Tumbi();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("tumbi");
		ui_interface->addHorizontalSlider("bite", &fHslider1, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("choke", &fHslider3, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(392.0f), FAUSTFLOAT(1.2e+02f), FAUSTFLOAT(2.5e+03f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider0, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = std::tan(fConst7 * (5.8e+03f * float(fHslider1) + 3.2e+03f) * (0.35f * fSlow0 + 0.65f));
		float fSlow2 = 2.0f * (1.0f - 1.0f / Tumbi_faustpower2_f(fSlow1));
		float fSlow3 = 1.0f / fSlow1;
		float fSlow4 = (fSlow3 + -1.4142135f) / fSlow1 + 1.0f;
		float fSlow5 = 1.0f / ((fSlow3 + 1.4142135f) / fSlow1 + 1.0f);
		float fSlow6 = float(fButton0);
		float fSlow7 = std::max<float>(1.2e+02f, float(fHslider2));
		int iSlow8 = int(std::max<float>(1.0f, fConst11 / fSlow7));
		float fSlow9 = 1.0f - fSlow3;
		float fSlow10 = 1.0f / (fSlow3 + 1.0f);
		float fSlow11 = 0.988f - 0.014f * float(fHslider3);
		float fSlow12 = std::max<float>(2.0f, fConst0 / fSlow7 + -2.0f);
		float fSlow13 = fSlow12 + -1.499995f;
		int iSlow14 = int(fSlow13);
		int iSlow15 = std::min<int>(2048, std::max<int>(0, iSlow14 + 4));
		float fSlow16 = std::floor(fSlow13);
		float fSlow17 = fSlow12 + (-3.0f - fSlow16);
		float fSlow18 = fSlow12 + (-2.0f - fSlow16);
		float fSlow19 = fSlow12 + (-1.0f - fSlow16);
		float fSlow20 = fSlow12 - fSlow16;
		float fSlow21 = fSlow20 * fSlow19;
		float fSlow22 = fSlow21 * fSlow18;
		float fSlow23 = 0.041666668f * fSlow22 * fSlow17;
		int iSlow24 = std::min<int>(2048, std::max<int>(0, iSlow14 + 3));
		float fSlow25 = 0.16666667f * fSlow22;
		int iSlow26 = std::min<int>(2048, std::max<int>(0, iSlow14 + 2));
		float fSlow27 = 0.25f * fSlow21;
		int iSlow28 = std::min<int>(2048, std::max<int>(0, iSlow14 + 1));
		float fSlow29 = 0.16666667f * fSlow20;
		int iSlow30 = std::min<int>(2048, std::max<int>(0, iSlow14));
		float fSlow31 = 0.041666668f * fSlow19;
		float fSlow32 = fSlow12 + (-4.0f - fSlow16);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow6;
			iRec3[0] = (iRec3[1] + (iRec3[1] > 0)) * (fSlow6 <= fVec0[1]) + (fSlow6 > fVec0[1]);
			float fTemp0 = float(iRec3[0]);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			float fTemp1 = float(iRec4[0]) * std::max<float>(0.0f, std::min<float>(fConst9 * fTemp0, fConst10 * (fConst8 - fTemp0) + 1.0f));
			fVec1[IOTA0 & 255] = fTemp1;
			fRec2[0] = 2.3283064e-10f * (fTemp1 - fVec1[(IOTA0 - iSlow8) & 255]) - fSlow5 * (fSlow4 * fRec2[2] + fSlow2 * fRec2[1]);
			fRec5[0] = -(fSlow10 * (fSlow9 * fRec5[1] - (fRec1[1] + fRec1[2])));
			float fTemp2 = fSlow11 * fRec5[0] + fSlow5 * (fRec2[2] + fRec2[0] + 2.0f * fRec2[1]);
			fVec2[IOTA0 & 2047] = fTemp2;
			fRec1[0] = fSlow32 * (fSlow17 * (fSlow18 * (fSlow31 * fVec2[(IOTA0 - iSlow30) & 2047] - fSlow29 * fVec2[(IOTA0 - iSlow28) & 2047]) + fSlow27 * fVec2[(IOTA0 - iSlow26) & 2047]) - fSlow25 * fVec2[(IOTA0 - iSlow24) & 2047]) + fSlow23 * fVec2[(IOTA0 - iSlow15) & 2047];
			fRec0[0] = fRec1[0] - fConst6 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp3 = fSlow0 * (0.82f * fRec1[0] + fConst12 * (fRec0[0] - fRec0[2]));
			output0[i0] = FAUSTFLOAT(fTemp3);
			output1[i0] = FAUSTFLOAT(fTemp3);
			fVec0[1] = fVec0[0];
			iRec3[1] = iRec3[0];
			iRec4[1] = iRec4[0];
			IOTA0 = IOTA0 + 1;
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec5[1] = fRec5[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
