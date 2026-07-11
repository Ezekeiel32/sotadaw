/* ------------------------------------------------------------
name: "harp"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Harp -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Harp_H__
#define  __Harp_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Harp
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

class HarpSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec6[2];
	
  public:
	
	int getNumInputsHarpSIG0() {
		return 0;
	}
	int getNumOutputsHarpSIG0() {
		return 1;
	}
	
	void instanceInitHarpSIG0(int sample_rate) {
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iVec2[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec6[l8] = 0;
		}
	}
	
	void fillHarpSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec6[0] = (iVec2[1] + iRec6[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec6[0]));
			iVec2[1] = iVec2[0];
			iRec6[1] = iRec6[0];
		}
	}

};

static HarpSIG0* newHarpSIG0() { return (HarpSIG0*)new HarpSIG0(); }
static void deleteHarpSIG0(HarpSIG0* dsp) { delete dsp; }

static float Harp_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0HarpSIG0[65536];

class Harp : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fHslider1;
	float fConst2;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst3;
	float fConst4;
	float fConst5;
	int iRec3[2];
	float fRec1[3];
	FAUSTFLOAT fHslider2;
	int iRec4[2];
	float fConst6;
	float fRec5[2];
	float fConst7;
	float fConst8;
	FAUSTFLOAT fHslider3;
	float fConst9;
	float fRec7[2];
	float fConst10;
	float fRec8[2];
	float fConst11;
	float fRec9[2];
	FAUSTFLOAT fHslider4;
	float fRec0[3];
	
 public:
	Harp() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Harp -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "harp.dsp");
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
		m->declare("name", "harp");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
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
		HarpSIG0* sig0 = newHarpSIG0();
		sig0->instanceInitHarpSIG0(sample_rate);
		sig0->fillHarpSIG0(65536, ftbl0HarpSIG0);
		deleteHarpSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		fConst2 = 14.137167f / fConst0;
		fConst3 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst4 = 1.0f / fConst3;
		fConst5 = 1.0f / std::max<float>(1.0f, 0.01f * fConst0);
		fConst6 = 1.0f / std::max<float>(1.0f, 0.2f * fConst0);
		fConst7 = std::max<float>(1.0f, 0.002f * fConst0);
		fConst8 = 1.0f / fConst7;
		fConst9 = 2.997f / fConst0;
		fConst10 = 2.002f / fConst0;
		fConst11 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(6.5e+03f);
		fHslider1 = FAUSTFLOAT(4.4e+02f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider2 = FAUSTFLOAT(0.55f);
		fHslider3 = FAUSTFLOAT(0.9f);
		fHslider4 = FAUSTFLOAT(0.65f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec3[l3] = 0;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec1[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec4[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec5[l6] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec7[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec8[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec9[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec0[l12] = 0.0f;
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
	
	virtual Harp* clone() {
		return new Harp();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("harp");
		ui_interface->addHorizontalSlider("decay", &fHslider3, FAUSTFLOAT(0.9f), FAUSTFLOAT(0.2f), FAUSTFLOAT(2.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.65f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("pluck", &fHslider2, FAUSTFLOAT(0.55f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("tone", &fHslider0, FAUSTFLOAT(6.5e+03f), FAUSTFLOAT(1.5e+03f), FAUSTFLOAT(1e+04f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / Harp_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -1.4142135f) / fSlow0 + 1.0f;
		float fSlow4 = (fSlow2 + 1.4142135f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = float(fHslider1);
		float fSlow7 = std::tan(fConst2 * fSlow6);
		float fSlow8 = 2.0f * (1.0f - 1.0f / Harp_faustpower2_f(fSlow7));
		float fSlow9 = 1.0f / fSlow7;
		float fSlow10 = (fSlow9 + -0.4f) / fSlow7 + 1.0f;
		float fSlow11 = (fSlow9 + 0.4f) / fSlow7 + 1.0f;
		float fSlow12 = 1.0f / fSlow11;
		float fSlow13 = float(fButton0);
		float fSlow14 = float(fHslider2) / (fSlow7 * fSlow11);
		int iSlow15 = fSlow13 == 0.0f;
		float fSlow16 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider3));
		float fSlow17 = fConst9 * fSlow6;
		float fSlow18 = fConst10 * fSlow6;
		float fSlow19 = fConst11 * fSlow6;
		float fSlow20 = float(fHslider4);
		float fSlow21 = 0.608f / fSlow4;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow13;
			iRec2[0] = (iRec2[1] + (iRec2[1] > 0)) * (fSlow13 <= fVec1[1]) + (fSlow13 > fVec1[1]);
			float fTemp0 = float(iRec2[0]);
			iRec3[0] = 1103515245 * iRec3[1] + 12345;
			fRec1[0] = 4.656613e-10f * float(iRec3[0]) * std::max<float>(0.0f, std::min<float>(fConst4 * fTemp0, fConst5 * (fConst3 - fTemp0) + 1.0f)) - fSlow12 * (fSlow10 * fRec1[2] + fSlow8 * fRec1[1]);
			iRec4[0] = iSlow15 * (iRec4[1] + 1);
			fRec5[0] = fSlow13 + fRec5[1] * float(fVec1[1] >= fSlow13);
			int iTemp1 = 1 - iVec0[1];
			float fTemp2 = ((iTemp1) ? 0.0f : fSlow17 + fRec7[1]);
			fRec7[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = ((iTemp1) ? 0.0f : fSlow18 + fRec8[1]);
			fRec8[0] = fTemp3 - std::floor(fTemp3);
			float fTemp4 = ((iTemp1) ? 0.0f : fSlow19 + fRec9[1]);
			fRec9[0] = fTemp4 - std::floor(fTemp4);
			fRec0[0] = fSlow20 * ((ftbl0HarpSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))] + 0.3f * ftbl0HarpSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec8[0]), 65535))] + 0.12f * ftbl0HarpSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))]) * std::max<float>(0.0f, std::min<float>(fConst8 * fRec5[0], std::max<float>(fSlow16 * (fConst7 - fRec5[0]) + 1.0f, 0.0f)) * (1.0f - fConst6 * float(iRec4[0]))) + fSlow14 * (fRec1[0] - fRec1[2])) - fSlow5 * (fSlow3 * fRec0[2] + fSlow1 * fRec0[1]);
			float fTemp5 = fSlow21 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp5);
			output1[i0] = FAUSTFLOAT(fTemp5);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			iRec3[1] = iRec3[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			iRec4[1] = iRec4[0];
			fRec5[1] = fRec5[0];
			fRec7[1] = fRec7[0];
			fRec8[1] = fRec8[0];
			fRec9[1] = fRec9[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
