/* ------------------------------------------------------------
name: "tanpura_drone"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn TanpuraDrone -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __TanpuraDrone_H__
#define  __TanpuraDrone_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS TanpuraDrone
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

class TanpuraDroneSIG0 {
	
  private:
	
	int iVec0[2];
	int iRec0[2];
	
  public:
	
	int getNumInputsTanpuraDroneSIG0() {
		return 0;
	}
	int getNumOutputsTanpuraDroneSIG0() {
		return 1;
	}
	
	void instanceInitTanpuraDroneSIG0(int sample_rate) {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec0[l1] = 0;
		}
	}
	
	void fillTanpuraDroneSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec0[0] = 1;
			iRec0[0] = (iVec0[1] + iRec0[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec0[0]));
			iVec0[1] = iVec0[0];
			iRec0[1] = iRec0[0];
		}
	}

};

static TanpuraDroneSIG0* newTanpuraDroneSIG0() { return (TanpuraDroneSIG0*)new TanpuraDroneSIG0(); }
static void deleteTanpuraDroneSIG0(TanpuraDroneSIG0* dsp) { delete dsp; }

static float ftbl0TanpuraDroneSIG0[65536];
static float TanpuraDrone_faustpower2_f(float value) {
	return value * value;
}

class TanpuraDrone : public dsp {
	
 private:
	
	int iVec1[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	float fConst2;
	float fConst4;
	float fConst5;
	float fRec4[2];
	FAUSTFLOAT fHslider2;
	float fConst8;
	FAUSTFLOAT fButton0;
	float fVec2[2];
	int iRec6[2];
	float fConst9;
	float fConst10;
	float fConst11;
	int iRec7[2];
	float fVec3[2];
	float fConst12;
	float fConst13;
	float fRec5[2];
	int IOTA0;
	float fVec4[8192];
	float fRec3[3];
	float fRec2[3];
	float fConst14;
	float fRec8[3];
	FAUSTFLOAT fHslider3;
	
 public:
	TanpuraDrone() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn TanpuraDrone -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
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
		m->declare("filename", "tanpura_drone.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
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
		m->declare("name", "tanpura_drone");
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
		TanpuraDroneSIG0* sig0 = newTanpuraDroneSIG0();
		sig0->instanceInitTanpuraDroneSIG0(sample_rate);
		sig0->fillTanpuraDroneSIG0(65536, ftbl0TanpuraDroneSIG0);
		deleteTanpuraDroneSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 0.6f / fConst0;
		fConst2 = 47.12389f / fConst0;
		float fConst3 = 1.0f / std::tan(23876.104f / fConst0);
		fConst4 = 1.0f - fConst3;
		fConst5 = 1.0f / (fConst3 + 1.0f);
		float fConst6 = std::tan(141.37167f / fConst0);
		float fConst7 = 1.0f / fConst6;
		fConst8 = 1.0f - fConst7;
		fConst9 = std::max<float>(1.0f, 0.004f * fConst0);
		fConst10 = 1.0f / fConst9;
		fConst11 = 1.0f / std::max<float>(1.0f, 0.03f * fConst0);
		fConst12 = 4.656613e-10f / fConst6;
		fConst13 = 1.0f / (fConst7 + 1.0f);
		fConst14 = 18.849556f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.5f);
		fHslider1 = FAUSTFLOAT(1.1e+02f);
		fHslider2 = FAUSTFLOAT(0.999f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider3 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iVec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec4[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fVec2[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec6[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iRec7[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fVec3[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec5[l9] = 0.0f;
		}
		IOTA0 = 0;
		for (int l10 = 0; l10 < 8192; l10 = l10 + 1) {
			fVec4[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec3[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec2[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec8[l13] = 0.0f;
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
	
	virtual TanpuraDrone* clone() {
		return new TanpuraDrone();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("tanpura_drone");
		ui_interface->addHorizontalSlider("buzz", &fHslider0, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(1.1e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("sustain", &fHslider2, FAUSTFLOAT(0.999f), FAUSTFLOAT(0.99f), FAUSTFLOAT(0.9999f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = 0.35f * fSlow0;
		float fSlow2 = float(fHslider1);
		float fSlow3 = fConst2 * fSlow2;
		float fSlow4 = float(fHslider2);
		float fSlow5 = float(fButton0);
		float fSlow6 = fConst0 / fSlow2;
		float fSlow7 = fSlow6 + -2.499995f;
		int iSlow8 = int(fSlow7);
		int iSlow9 = std::min<int>(4096, std::max<int>(0, iSlow8 + 4));
		float fSlow10 = std::floor(fSlow7);
		float fSlow11 = fSlow6 + (-4.0f - fSlow10);
		float fSlow12 = fSlow6 + (-3.0f - fSlow10);
		float fSlow13 = fSlow6 + (-2.0f - fSlow10);
		float fSlow14 = fSlow6 + (-1.0f - fSlow10);
		float fSlow15 = fSlow14 * fSlow13;
		float fSlow16 = fSlow15 * fSlow12;
		float fSlow17 = 0.041666668f * fSlow16 * fSlow11;
		int iSlow18 = std::min<int>(4096, std::max<int>(0, iSlow8 + 3));
		float fSlow19 = 0.16666667f * fSlow16;
		int iSlow20 = std::min<int>(4096, std::max<int>(0, iSlow8 + 2));
		float fSlow21 = 0.25f * fSlow15;
		int iSlow22 = std::min<int>(4096, std::max<int>(0, iSlow8 + 1));
		float fSlow23 = 0.16666667f * fSlow14;
		int iSlow24 = std::min<int>(4096, std::max<int>(0, iSlow8));
		float fSlow25 = 0.041666668f * fSlow13;
		float fSlow26 = fSlow6 + (-5.0f - fSlow10);
		float fSlow27 = fConst14 * fSlow2;
		float fSlow28 = 1e+01f * fSlow0 + 3.0f;
		float fSlow29 = 0.62f * fSlow0;
		float fSlow30 = 0.42f * float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec1[0] = 1;
			float fTemp0 = ((1 - iVec1[1]) ? 0.0f : fConst1 + fRec1[1]);
			fRec1[0] = fTemp0 - std::floor(fTemp0);
			float fTemp1 = fSlow1 * ftbl0TanpuraDroneSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec1[0]), 65535))] + 1.0f;
			float fTemp2 = std::tan(fSlow3 * fTemp1);
			float fTemp3 = 1.0f / fTemp2;
			float fTemp4 = (fTemp3 + 0.09090909f) / fTemp2 + 1.0f;
			fRec4[0] = -(fConst5 * (fConst4 * fRec4[1] - (fRec3[1] + fRec3[2])));
			fVec2[0] = fSlow5;
			iRec6[0] = (iRec6[1] + (iRec6[1] > 0)) * (fSlow5 <= fVec2[1]) + (fSlow5 > fVec2[1]);
			float fTemp5 = float(iRec6[0]);
			iRec7[0] = 1103515245 * iRec7[1] + 12345;
			float fTemp6 = float(iRec7[0]) * std::max<float>(0.0f, std::min<float>(fConst10 * fTemp5, fConst11 * (fConst9 - fTemp5) + 1.0f));
			fVec3[0] = fTemp6;
			fRec5[0] = fConst13 * (fConst12 * (fTemp6 - fVec3[1]) - fConst8 * fRec5[1]);
			float fTemp7 = fRec5[0] + fSlow4 * fRec4[0];
			fVec4[IOTA0 & 8191] = fTemp7;
			fRec3[0] = fSlow26 * (fSlow11 * (fSlow12 * (fSlow25 * fVec4[(IOTA0 - iSlow24) & 8191] - fSlow23 * fVec4[(IOTA0 - iSlow22) & 8191]) + fSlow21 * fVec4[(IOTA0 - iSlow20) & 8191]) - fSlow19 * fVec4[(IOTA0 - iSlow18) & 8191]) + fSlow17 * fVec4[(IOTA0 - iSlow9) & 8191];
			fRec2[0] = fRec3[0] - (fRec2[2] * ((fTemp3 + -0.09090909f) / fTemp2 + 1.0f) + 2.0f * fRec2[1] * (1.0f - 1.0f / TanpuraDrone_faustpower2_f(fTemp2))) / fTemp4;
			float fTemp8 = std::tan(fSlow27 * fTemp1);
			float fTemp9 = 1.0f / fTemp8;
			float fTemp10 = (fTemp9 + 0.125f) / fTemp8 + 1.0f;
			fRec8[0] = fRec3[0] - (fRec8[2] * ((fTemp9 + -0.125f) / fTemp8 + 1.0f) + 2.0f * fRec8[1] * (1.0f - 1.0f / TanpuraDrone_faustpower2_f(fTemp8))) / fTemp10;
			float fTemp11 = tanhf(fSlow30 * (0.78f * fRec3[0] + fSlow29 * tanhf(fSlow28 * ((fRec8[0] - fRec8[2]) / (fTemp8 * fTemp10) + 0.9f * ((fRec2[0] - fRec2[2]) / (fTemp2 * fTemp4))))));
			output0[i0] = FAUSTFLOAT(fTemp11);
			output1[i0] = FAUSTFLOAT(fTemp11);
			iVec1[1] = iVec1[0];
			fRec1[1] = fRec1[0];
			fRec4[1] = fRec4[0];
			fVec2[1] = fVec2[0];
			iRec6[1] = iRec6[0];
			iRec7[1] = iRec7[0];
			fVec3[1] = fVec3[0];
			fRec5[1] = fRec5[0];
			IOTA0 = IOTA0 + 1;
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec8[2] = fRec8[1];
			fRec8[1] = fRec8[0];
		}
	}

};

#endif
